// Shiny-Button — Pwny-CTF (script de solve)
<!DOCTYPE html>
<html>
<head>
  <title>MD5 Hashing</title>
  <!-- Adapted from the SecureState 2015 High School CTF  http://www.mountunion.edu/information-security-challenge-slated-for-saturday  -->
  <!-- Originally hosted at http://warroom.securestate.com -->
</head>
<body>
  <p>Cryptographic hashing functions, such as MD5 and SHA-1, have multiple uses, but are often used to verify data integrity.
  </p>
  <p>MD5 hashes are typically represented as 32 hexadecimal digits.  The length of the hash is not dependent on the input.  Whether you compute the MD5 hash of a short word or a large file, the resulting hash will be 32 hexadecimal digits in length.  In that way, hashing is different than encoding, encrypting, or compressing - one is not intended to be able to recover the data value from the hash.
  </p>
  <p>Enter some text in the form below to see its MD5 hash.  Try words and strings of different lengths to see how they result in hashes that are the same length.  Also, experiment to see how making slight changes to a string results in a completely different hash value.
  </p>
    <p><form action="index.php" method="get">
    String to Hash:<input type="text" name="string" value="hash me!">
    <input type="submit">
    </form>
    <br />
    <b>MD5 Hash:  </b>
    <?php
    echo shell_exec('echo '.$_GET['string'].' | md5sum');
    ?>
    <br /><br />
    </p>
    <p>To read more about the MD5 hashing function, visit <a href="http://en.wikipedia.org/wiki/MD5">Wikipedia</a>.
    </p>
</body>
</html>
