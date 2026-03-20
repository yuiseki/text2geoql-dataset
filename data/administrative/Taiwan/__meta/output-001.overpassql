// Important note: SubArea: Taiwan
[out:json][timeout:30];
area["name:en"="Taiwan"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=4](area.searchArea);
);
out meta;
