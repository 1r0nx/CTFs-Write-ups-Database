#include <stdio.h>
#include <stdint.h>
#include <omp.h>
// Emule le programme PIO simple_pio sur une entree 32 bits.
// 8 iterations, chacune consomme 1+3 bits de l'OSR et pousse 3+1 bits dans l'ISR.
// Par iteration : out(x,1); out(y,3); si x: y_dec (y-- si y>0); mov(y,~y); in(y,3); in(x,1)
// conv: 0 = shift right (LSB first), 1 = shift left (MSB first) pour OUT et IN.
static inline uint32_t pio(uint32_t v, int outdir, int indir){
    uint32_t osr=v, isr=0;
    for(int it=0; it<8; it++){
        uint32_t x,y;
        if(outdir==0){ x=osr&1; osr>>=1; y=osr&7; osr>>=3; }
        else { x=(osr>>31)&1; osr=(osr<<1)&0xffffffff; y=(osr>>29)&7; osr=(osr<<3)&0xffffffff; }
        if(x){ y=(y-1)&0xffffffff; }           // y_dec seulement si x==1
        uint32_t yout=(~y)&7, xout=x&1;
        // in(y,3) puis in(x,1)
        if(indir==0){ isr=(isr>>3)|(yout<<29); isr=(isr>>1)|(xout<<31); }
        else { isr=((isr<<3)|yout)&0xffffffff; isr=((isr<<1)|xout)&0xffffffff; }
    }
    return isr;
}
int main(void){
    const uint32_t target=0x122c5bf4u;
    #pragma omp parallel for schedule(dynamic,2000000)
    for(long long v=0; v<=0xffffffffLL; v++){
        uint32_t u=(uint32_t)v;
        for(int od=0; od<2; od++) for(int id=0; id<2; id++)
            if(pio(u,od,id)==target){
                #pragma omp critical
                printf("key=0x%08x outdir=%d indir=%d\n",u,od,id);
            }
    }
    return 0;
}
