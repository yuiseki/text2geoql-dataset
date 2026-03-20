// Important note: SubArea: Taiwan/Taipei
[out:json][timeout:30];
area["name:en"="Taipei"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
