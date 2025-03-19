#include <iostream>
#include <fstream>
#include <set>
#include <string>
#include <iterator>

int main() {
   // You can put here your file's path
   std::ifstream inputFile("admin_path.txt");
   
   if (!inputFile) {
      std::cerr << "Error opening file 'admin_path.txt'!" << std::endl;
      return 1;
   }

   std::set<std::string> uniqueLines;
   std::string line;

   while (std::getline(inputFile, line)) {
      uniqueLines.insert(line);
   }
   
   inputFile.close();

   std::ofstream outputFile("admin_path.txt");

   if (!outputFile) {
      std::cerr << "Error opening file 'admin_path.txt' for writing!" << std::endl;
      return 1;
   }

   for (const auto& uniqueLine : uniqueLines) {
      outputFile << uniqueLine << std::endl;
   }

   outputFile.close();
   std::cout << "Duplicates removed and file updated successfully!" << std::endl;

   return 0;
}