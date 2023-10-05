#include <SPI.h>
#include <SD.h>

File root;
File dataFile;

void setup() {
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  Serial.print("Initializing SD card...");

  if (!SD.begin(4)) {
    Serial.println("Initialization failed!");
    while (1);
  }
  Serial.println("Initialization done.");

  root = SD.open("/");
  printDirectory(root, 0);

  // Open file and display its contents
  dataFile = SD.open("file.txt");
  if (dataFile) {
    while (dataFile.available()) {
      char dataChar = dataFile.read();
      Serial.write(dataChar);
    }
    dataFile.close();
  } else {
    Serial.println("Error opening the file");
  }
}

void loop() {
  // Nothing happens after setup finishes.
}

void printDirectory(File dir, int numTabs) {
  while (true) {
    File entry = dir.openNextFile();
    if (!entry) {
      // No more files
      break;
    }
    for (uint8_t i = 0; i < numTabs; i++) {
      Serial.print('\t');
    }
    Serial.print(entry.name());
    if (entry.isDirectory()) {
      Serial.println("/");
      printDirectory(entry, numTabs + 1);
    } else {
      // Files have sizes, directories do not
      Serial.print("\t\t");
      Serial.println(entry.size(), DEC);
    }
    entry.close();
  }
}



