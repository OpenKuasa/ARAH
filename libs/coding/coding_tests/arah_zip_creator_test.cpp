#include "testing/testing.hpp"

#include "coding/file_writer.hpp"
#include "coding/internal/file_data.hpp"
#include "coding/zip_creator.hpp"
#include "coding/zip_reader.hpp"

#include "base/scope_guard.hpp"

#include <string>
#include <vector>

namespace arah_zip_creator_test
{
// Shared bookmark archives rename non-ASCII entries; the fallback names carry Arah's name.
UNIT_TEST(Arah_CreateZip_NonAsciiNamesUseArah)
{
  std::vector<std::string> const files{"arah_zip_1.kml", "arah_zip_2.kml"};
  std::vector<std::string> const filesInArchive{"Üφήが1.kml", "Üφήが2.kml"};
  std::string const zipPath = "arah_zip_test.kmz";
  SCOPE_GUARD(deleteFilesGuard, [&]()
  {
    for (auto const & file : files)
      base::DeleteFileX(file);
    base::DeleteFileX(zipPath);
  });

  for (auto const & name : files)
  {
    FileWriter f(name);
    f.Write(name.c_str(), name.size());
  }

  TEST(CreateZipFromFiles(files, filesInArchive, zipPath, CompressionLevel::DefaultCompression), ());

  ZipFileReader::FileList fileList;
  ZipFileReader::FilesList(zipPath, fileList);
  TEST_EQUAL(fileList.size(), 2, ());
  TEST_EQUAL(fileList[0].first, "Arah.kml", ());
  TEST_EQUAL(fileList[1].first, "Arah_1.kml", ());
}
}  // namespace arah_zip_creator_test
