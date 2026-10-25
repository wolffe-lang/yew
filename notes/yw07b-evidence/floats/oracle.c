/* Black-box C11 libc calls, matching sagitta 9ace98c2 conversion sites:
 * stdfmt.c:169-236, stdstr.c:903-913, lex.c:347, dump.c:275.
 * This harness calls the public API; no libc/library source was read. */
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int64_t bits(double x) { int64_t n; memcpy(&n, &x, sizeof(n)); return n; }
static void shortest(double x) {
    char buf[64]; int p;
    for (p=15; p<=17; ++p) {
        (void)snprintf(buf, sizeof(buf), "%.*g", p, x);
        if (strtod(buf, NULL)==x) break;
    }
    char *e=strchr(buf,'e');
    printf("shortest:0:");
    if (e) {
        *e='\0'; printf("%s%s",buf,strchr(buf,'.')?"":".0");
        printf("e%s\n",e+1);
    } else printf("%s%s\n",buf,strchr(buf,'.')?"":".0");
}
int main(void) {
    char line[4096];
    while (fgets(line,sizeof(line),stdin)) {
        size_t len=strlen(line); if (len && line[len-1]=='\n') line[--len]='\0';
        if (line[0]=='P') {
            char *end; double x=strtod(line+2,&end);
            printf("parse:%td:%" PRId64 "\n",end-(line+2),bits(x));
        } else {
            int64_t n=strtoll(line+2,NULL,10); double x;
            memcpy(&x,&n,sizeof(x));
            printf("bits:0:%" PRId64 "\n",bits(x));
            for (int p=0;p<=17;++p) {
                printf("fixed:%d:%.*f\n",p,p,x);
                printf("exp:%d:%.*e\n",p,p,x);
            }
            for (int p=15;p<=17;++p) printf("general:%d:%.*g\n",p,p,x);
            shortest(x);
        }
    }
    return ferror(stdin) || ferror(stdout) ? 1 : 0;
}
