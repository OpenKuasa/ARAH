package app.organicmaps.sdk.util;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

/**
 * Arah has no domain for share links yet, so places are shared as OpenStreetMap links
 * (libs/map/arah_share.hpp), the same as on iPhone.
 */
public final class ArahShare
{
  private ArahShare() {}

  /**
   * @param zoomLevel 0 or less means the current map scale.
   * @return https://www.openstreetmap.org/?mlat=..&mlon=..#map=zoom/lat/lon
   */
  @NonNull
  public static String getShareLink(double lat, double lon, double zoomLevel)
  {
    return nativeShareLink(lat, lon, zoomLevel);
  }

  /**
   * @param zoomLevel 0 or less means the current map scale.
   * @return "name\ndetails\nlat, lon\nlink", skipping an empty name or details line.
   */
  @NonNull
  public static String getShareText(@NonNull String name, @NonNull String details, double lat, double lon,
                                    double zoomLevel)
  {
    return nativeShareText(name, details, lat, lon, zoomLevel);
  }

  /**
   * @return the non-empty lines joined with "\n", as the place details on iPhone.
   */
  @NonNull
  public static String joinLines(@Nullable String... lines)
  {
    final StringBuilder sb = new StringBuilder();
    for (String line : lines)
    {
      if (line == null || line.isEmpty())
        continue;
      if (sb.length() > 0)
        sb.append('\n');
      sb.append(line);
    }
    return sb.toString();
  }

  /**
   * @param phones OpenStreetMap phone numbers separated by ';'.
   * @return the numbers separated by "; ", as on iPhone.
   */
  @NonNull
  public static String formatPhones(@Nullable String phones)
  {
    if (phones == null)
      return "";
    final StringBuilder sb = new StringBuilder();
    for (String phone : phones.split(";"))
    {
      final String trimmed = phone.trim();
      if (trimmed.isEmpty())
        continue;
      if (sb.length() > 0)
        sb.append("; ");
      sb.append(trimmed);
    }
    return sb.toString();
  }

  @NonNull
  private static native String nativeShareLink(double lat, double lon, double zoomLevel);

  @NonNull
  private static native String nativeShareText(@NonNull String name, @NonNull String details, double lat, double lon,
                                               double zoomLevel);
}
