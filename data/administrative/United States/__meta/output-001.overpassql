// Important note: SubArea: United States
[out:json][timeout:30000];
area["name:en"="United States"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=4](area.searchArea);
);
out meta;
