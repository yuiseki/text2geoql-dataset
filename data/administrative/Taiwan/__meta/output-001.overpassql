// Important note: SubArea: Taiwan
[out:json][timeout:30000];
area["name:en"="Taiwan"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=4](area.searchArea);
);
out geom;
