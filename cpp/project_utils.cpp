#include <cctype>

extern "C" {

bool valid_name(const char* name) {
    if (!name || name[0] == '\0') return false;
    for (int i = 0; name[i]; i++) {
        if (!isalnum(name[i]) && name[i] != '-' && name[i] != '_')
            return false;
    }
    return true;
}

}
