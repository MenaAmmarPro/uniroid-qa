#include <stdio.h>
#include <string.h>

int main(int argc, char** argv) {
    if (argc < 2) { fprintf(stderr, "usage: helper <logfile>\n"); return 1; }
    FILE* f = fopen(argv[1], "r");
    if (!f) { perror("fopen"); return 1; }
    char line[4096];
    int crashes = 0, anrs = 0, lines = 0;
    while (fgets(line, sizeof(line), f)) {
        lines++;
        if (strstr(line, "FATAL EXCEPTION")) crashes++;
        if (strstr(line, "ANR in")) anrs++;
    }
    fclose(f);
    printf("lines=%d crashes=%d anrs=%d\n", lines, crashes, anrs);
    return (crashes + anrs) > 0 ? 2 : 0;
}
