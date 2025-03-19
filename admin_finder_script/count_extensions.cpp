#include <iostream>
#include <fstream>
#include <unordered_map>
#include <string>
#include <sstream>

std::string get_extension(const std::string& file_name) {
   size_t pos = file_name.rfind('.');
   if (pos != std::string::npos) {
      return file_name.substr(pos + 1); 
   }
   return "";
}

int main() {
   std::ifstream inputFile("admin_path.txt");
   
   if (!inputFile) {
      std::cerr << "Error opening file 'admin_path.txt'!" << std::endl;
      return 1;
   }

   std::unordered_map<std::string, int> extensionCount;
   std::string line;

   while (std::getline(inputFile, line)) {
      std::string ext = get_extension(line);
      if (!ext.empty()) {
         extensionCount[ext]++; 
      }
   }
   
   inputFile.close();

   std::cout << "File extensions and their counts:" << std::endl;
   for (const auto& pair : extensionCount) {
      std::cout << "." << pair.first << ": " << pair.second << std::endl;
   }

   return 0;
}