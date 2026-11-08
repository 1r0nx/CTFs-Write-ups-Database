/*
 * ravi (jprx) heap challenge 4
 *
 * This challenge involves creating overlapping chunks by exploiting
 * a heap buffer overwrite to mess with the metadata of an adjacent
 * chunk. Use the metadata to manipulate the tcache size.
 *
 * This time around we're using tcaches, not fastbins. Also,
 * documents fall into a different bin than users, so they'll
 * never be allocated to the same chunk.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>

// Length of the user input buffer:
#define USERBUF_LEN ((128))

// Length of a username:
#define NAME_LEN ((60))

// Length of a document:
#define DOCUMENT_LEN ((80))

/*
 * user_t
 *
 * A user in the system.
 * A list of users is maintained in an array.
 * If any user's logged_in field is set to true (non-zero), then
 * that user is effectively logged in, and can be switched to.
 */
typedef struct user_struct_t {
    char name[NAME_LEN];
    uint32_t logged_in;
} user_t;

/*
 * document_t
 *
 * A document being written.
 * Documents are not owned by any user, they just exist.
 */
typedef struct document_struct_t {
    char text[DOCUMENT_LEN];
} document_t;

/*
 * choice_t
 *
 * User's choice for action
 */
typedef enum input_choice_enum_t {
    CREATE_USER = 0,
    SWITCH_USER,
    SHOW_USERS,
    DEL_USER,

    CREATE_DOC,
    WRITE_DOC,
    SHOW_DOCS,

    SHELL,

    HELP,
    INFO,
    EXIT,

    NUM_CHOICES,
    INVALID = 128
} choice_t;

/*
 * options
 *
 * Valid commands
 */
const char options[][32] = {
    "create_user",
    "switch_user",
    "show_users",
    "del_user",

    "create_doc",
    "write_doc",
    "show_docs",

    "shell",

    "help",
    "info",
    "exit"
};

/*
 * Global application state.
 *
 * I wonder if we could corrupt these data structures...? :P
 */

#define NUM_USERS ((32))
#define NUM_DOCUMENTS ((32))

// Array of pointers to users:
user_t *users[NUM_USERS];
static unsigned int num_users = 0;

// Selected user, now featuring pointers(TM)!
static user_t *current_user;

// Array of pointers to documents:
document_t *documents[NUM_DOCUMENTS];
static unsigned int num_documents = 0;

/*
 * disable_buffering
 *
 * Disable input buffers
 */
void disable_buffering (void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

/*
 * show_help
 *
 * Shows a help screen to the user.
 */
void show_help(void) {
    const char logo[] = "\n"
"██╗  ██╗███████╗ █████╗ ██████╗ ██╗  ██╗\n"
"██║  ██║██╔════╝██╔══██╗██╔══██╗██║  ██║\n"
"███████║█████╗  ███████║██████╔╝███████║\n"
"██╔══██║██╔══╝  ██╔══██║██╔═══╝ ╚════██║\n"
"██║  ██║███████╗██║  ██║██║          ██║\n"
"╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝          ╚═╝\n";

    printf(logo);
    // printf("---------------------------------------------------------\n");
    printf("Welcome to SIGPwny heap level 4!\nCommands:\n");
    printf("\nUser commands:\n");
    printf("\tcreate_user {NAME}\tCreates a new user. If a user with the same name exists,\n\t\t\t\tnothing happens.\n");
    printf("\tswitch_user {ID}\tSwitches to a new user account. (they must be logged in)\n");
    printf("\tshow_users\t\tShows all users\n");
    printf("\tdel_user {ID}\t\tDeletes a user account.\n");
    printf("\nDocument commands:\n");
    printf("\tcreate_doc\t\tCreates a new document\n");
    printf("\twrite_doc {ID} {text}\tWrite into a document\n");
    printf("\tshow_docs\t\tShows all documents\n");
    printf("\nGeneral commands:\n");
    printf("\tshell\t\t\tOpens a root shell. Need to be 'admin' to do this!\n");
    printf("\thelp\t\t\tShow the help screen.\n");
    printf("\tinfo\t\t\tShow some info about program internals.\n");
    printf("\texit\t\t\tExit this app.\n");
    printf("\n");
}

/*
 * assert_facts
 *
 * Ensure sizes & stuff are correct.
 */
void assert_facts(void) {
    assert(sizeof(user_t) != sizeof(document_t));
    assert(NUM_CHOICES == 11);
}

/*
 * clear_arrays
 *
 * Just clears the arrays
 */
void clear_arrays(void) {
    for (int i = 0; i < NUM_USERS; i++) {
        users[i] = NULL;
    }

    for (int i = 0; i < NUM_DOCUMENTS; i++) {
        documents[i] = NULL;
    }
}

/*
 * create_user
 *
 * Creates a new user and returns a pointer to it.
 */
user_t *create_user(char *name_in) {
    user_t *new_user = NULL;

    if (num_users < NUM_USERS) {
        new_user = malloc(sizeof(*new_user));

        if (new_user != NULL) {
            strncpy(new_user->name, name_in, NAME_LEN);
            new_user->logged_in = 0;

            // Insert user into the users list
            users[num_users] = new_user;
            num_users++;
        }
    }

    return new_user;
}

/*
 * get_arg
 *
 * Converts the provided string to an int
 */
int get_arg(char *str) {
    int arg1 = -1;

    if (str == NULL) { return -2; }

    if (str != NULL) {
        if (!sscanf(str, "%d", &arg1)) {
            return -1;
        }
    }

    return arg1;
}

/*
 * is_user_in_table
 *
 * Returns true if the user pointer provided is in the users table, false otherwise.
 */
bool is_user_in_table (user_t *u) {
    for (int i = 0; i < NUM_USERS; i++) {
        if (users[i] == u) return true;
    }

    return false;
}

/*
 * is_doc_in_table
 *
 * Returns true if the document pointer provided is in the documents table, false otherwise.
 */
bool is_doc_in_table (document_t *d) {
    for (int i = 0; i < NUM_DOCUMENTS; i++) {
        if (documents[i] == d) return true;
    }

    return false;
}

/*
 * switch_user
 *
 * Switch currently logged in user to another user ID, assuming
 * that account is logged in in this session.
 */
void switch_user (int id) {
    if (id >=0 && id < NUM_USERS) {
        if (users[id] != NULL) {
            if (users[id]->logged_in) {
                current_user = users[id];
                printf("Logged in as %s\n", users[id]->name);
            }
            else {
                printf("That user isn't logged in! Can't switch to their account!\n");
            }
        }
        else {
            printf("No such user\n");
        }
    }
}

/*
 * show_info
 *
 * Show a little more info about the program to help people develop exploits :)
 */
void show_info(void) {
    printf("SIGPwny Heap Challenges by ravi (jprx)\n");
    printf("These challenges are deployed on Ubuntu 20.04, which should be running glibc 2.31\n");
    printf("\n");
    printf("struct user_t {\n\tchar name[60]; // 60 bytes\n\tuint32_t logged_in; // 4 bytes\n};\n");
    printf("\n");
    printf("struct document_t {\n\tchar text[80]; // 80 bytes\n};\n");
    printf("\n");
}

/*
 * handle_choice
 *
 * Handles a user's choice and performs an appropriate response.
 */
void handle_choice (choice_t choice, char *arg1_string, size_t arg1_len) {
    user_t *new_user;
    document_t *new_document;
    int arg1;
    char *cursor = arg1_string;
    char *doc_contents = NULL;

    switch(choice) {
        case CREATE_USER:
            if (!arg1_string) {
                printf("Need to give a name!\n");
                return;
            }

            for (int i = 0; i < NUM_USERS; i++) {
                if (users[i] != NULL) {
                    if (!strncmp(arg1_string, users[i]->name, NAME_LEN)) {
                        printf("User exists already!\n");
                        return;
                    }
                }
            }

            // Create a new user and mark it as logged in.
            new_user = create_user(arg1_string);

            if (new_user != NULL) {
                new_user->logged_in = 1;
                printf("Created user %d\n", num_users-1);
            }
        break;

        case SWITCH_USER:
            arg1 = get_arg(arg1_string);
            if (arg1 < 0) {
                printf("Invalid argument! (Need to use index, not name)\n\n");
                return;
            }
            switch_user(arg1);
            printf("\n");
        break;

        case SHOW_USERS:
            printf("+--------------------------------+\n");
            printf("| id: (name, logged_in, address) |\n");
            printf("+--------------------------------+\n");
            for (int i = 0; i < NUM_USERS; i++) {
                if (users[i] != NULL) {
                    printf("%d: ('%s', %d, %p)", i, users[i]->name, users[i]->logged_in, users[i]);

                    if (current_user == users[i]) {
                        printf(" <-- selected user");
                    }
                    printf("\n");
                }
            }
            printf("\n");
        break;

        case DEL_USER:
            arg1 = get_arg(arg1_string);
            if (arg1 < 0) {
                printf("Invalid argument!\n\n");
                return;
            }

            if (arg1 < NUM_USERS && arg1 >= 0) {
                if (users[arg1] != NULL) {
                    if (!users[arg1]->logged_in) {
                        printf("Can't delete this user as they aren't logged in!\n\n");
                        return;
                    }
                    if (users[arg1] == current_user) {
                        printf("Can't delete the currently selected user!\n\n");
                        return;
                    }
                    printf("Deleted user %d (named %s)\n\n", arg1, users[arg1]->name);
                    users[arg1]->logged_in = 0;

                    // If this user is in the documents table for some reason, remove it from there too
                    for (int j = 0; j < NUM_DOCUMENTS; j++) {
                        if (documents[j] == (document_t *)users[arg1]) {
                            documents[j] = NULL;
                        }
                    }

                    free(users[arg1]);
                    users[arg1] = NULL;
                }
                else {
                    printf("No such user\n\n");
                }
            }
        break;

        case CREATE_DOC:
            if (num_documents < NUM_DOCUMENTS) {
                // Create a new document
                new_document = malloc(sizeof(*new_document));

                if (new_document != NULL) {
                    documents[num_documents] = new_document;
                    num_documents++;
                    printf("Created document %d\n", num_documents - 1);
                    return;
                }
            }

            printf("Couldn't create a document\n\n");

        break;

        case WRITE_DOC:
            cursor = arg1_string;
            doc_contents = NULL;

            // Split document number from contents to write
            // Subtract docoument number from # of bytes to write
            while (*cursor) {
                if (*cursor == ' ' && *(cursor + 1) != '\0') { doc_contents = cursor+1; arg1_len--; break; }
                cursor++;
                arg1_len--;
            }

            arg1 = get_arg(arg1_string);
            if (arg1 < 0) {
                printf("Invalid document!\n");
                return;
            }

            if (doc_contents == NULL) {
                printf("Need something to write!\n");
                return;
            }

            // Artificial 10 byte overwrite
            if (arg1_len > DOCUMENT_LEN + 10) {
                arg1_len = DOCUMENT_LEN + 10;
                doc_contents[DOCUMENT_LEN-1 + 10] = '\0';
            }

            if (arg1 >= 0 && arg1 < num_documents) {
                if (documents[arg1] != NULL) {
                    printf("[document %d] writing %s\n", arg1, doc_contents);
                    memcpy(documents[arg1]->text, doc_contents, arg1_len);
                }
            }
            else {
                printf("No such document\n\n");
            }
        break;

        case SHOW_DOCS:
            if(num_documents == 0) {
                printf("No documents yet. Create one with 'create_doc'!\n\n");
            }

            for (int i = 0; i < NUM_DOCUMENTS; i++) {
                if (documents[i] != NULL) {
                    cursor = (char *)&documents[i]->text;
                    printf("+------ %02d ------+\n", i);
                    // printf("|    Address:    |\n");
                    printf("| %p |\n", documents[i]);
                    // printf("|    Contents:   |\n");

                    for (int j = 0; j < (DOCUMENT_LEN)/16; j++) {
                        printf("|");
                        for (int k = 0; k < 16; k++) {
                            if (*cursor) {
                                printf("%c", *cursor);
                            }
                            else {
                                printf(" ");
                            }
                            cursor++;
                        }
                        printf("|\n");
                    }
                    printf("+----------------+\n");
                }
            }
        break;

        case SHELL:
            if (!strncmp(current_user->name, "admin", NAME_LEN)) {
                // Prevent user from simply deleting selected, creating a new doc, and yeeting to admin
                // This check is probably unnecessary for this challenge, but will also prevent unintentional
                // memory corruption vulnerabilities from working here too.
                if (!is_user_in_table(current_user)) {
                    printf("Currently selected user isn't in the table...\nDid you corrupt memory somehow?\n\n");
                    return;
                }
                printf("Ok here's a shell:\n");
                system("/bin/sh");
            }
            else {
                printf("Need to be logged in as 'admin' to do that!\n\n");
            }
        break;

        case HELP:
            show_help();
        break;

        case INFO:
            show_info();
        break;

        case EXIT:
            exit(0);
        break;

        case INVALID:
            printf("Invalid command!\n");
        break;
    }
}

/*
 * get_choice
 *
 * Prompts the user for a choice and handles the response.
 */
void get_choice (void) {
    char userbuf[USERBUF_LEN];
    char *cursor;
    char *arg1;
    choice_t choice;

    if (current_user == NULL) {
        printf("You're somehow not logged in as any user, this shouldn't be possible!\n");
        exit(-1);
    }

    printf("%s > ", current_user->name);
    memset(userbuf, '\0', sizeof(userbuf));
    size_t arg1_len = read(0, userbuf, sizeof(userbuf));

    // Strip newline & detect the argument
    cursor = userbuf;
    arg1 = NULL;
    while (cursor && *cursor) {
        if (*cursor == '\n') { *cursor = '\0'; break; }
        if (*cursor == ' ' && (*(cursor + 1) != '\0') && (*(cursor + 1) != '\n')) {
            *cursor = '\0';
            arg1 = cursor + 1;
            arg1_len--;
            break;
        }
        cursor++;
        arg1_len--;
    }

    cursor = arg1;
    while (cursor && *cursor) {
        if (*cursor == '\n') { *cursor = '\0'; break; }
        cursor++;
    }
    
    choice = INVALID;
    for (int i = 0; i < NUM_CHOICES; i++) {
        if (!strncmp(userbuf, options[i], sizeof(userbuf))) {
            choice = (choice_t) i;
        }
    }

    handle_choice(choice, arg1, arg1_len);
}

/*
 * fill_tcaches
 *
 * Fills up the tcaches so all our allocations go in fastbins
 */
void fill_tcaches(void) {
    // printf("There's a neat optimization in Glibc >= 2.27 called 'tcaches'\n");
    // printf("We don't want to deal with them now though, so we are going to\n");
    // printf("fill them up artificially so they don't interfere with the challenge.\n\n");
    void *ptrs[8];
    for (int i = 0; i < 8; i++) {
        ptrs[i] = malloc(64);
    }
    for (int i = 0; i < 8; i++) {
        free(ptrs[i]);
    }

    for (int i = 0; i < 8; i++) {
        ptrs[i] = malloc(80);
    }
    for (int i = 0; i < 8; i++) {
        free(ptrs[i]);
    }
}

/*
 * main
 *
 * Handle application logic.
 */
int main () {
    assert_facts();
    disable_buffering();
    show_help();
    clear_arrays();

    // We want tcaches for heap 4:
    // fill_tcaches();

    user_t *admin = create_user("admin");
    admin->logged_in = 0;

    user_t *default_user = create_user("sigpwny");
    default_user->logged_in = 1;
    switch_user(1);

    while (1) {
        get_choice();
    }
}
