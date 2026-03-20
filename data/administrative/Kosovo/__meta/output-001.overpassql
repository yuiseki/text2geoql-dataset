// Important note: SubArea: Kosovo
[out:json][timeout:30];
area["name:en"="Kosovo"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=4](area.searchArea);
);
out meta;
