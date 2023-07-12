#include <iostream>
#include <string>
#include <filesystem>
#include <unistd.h>

using std::cout; using std::cin;
using std::endl; using std::string;
using std::filesystem::current_path;

int main() {
    char tmp[256];
    getcwd(tmp, 256);
    cout << "Current working directory: " << tmp << endl;

    return EXIT_SUCCESS;
}