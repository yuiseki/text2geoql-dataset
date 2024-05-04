// Important note: SubArea: Japan/Niigata Prefecture
[out:json][timeout:30000];
area["name:en"="Niigata Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
