// Important note: SubArea: Japan/Osaka Prefecture
[out:json][timeout:30000];
area["name:en"="Osaka Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
