[out:json][timeout:30000];
area["name:en"="Kosovo"]->.searchArea;
(
  nwr["office"="diplomatic"](area.searchArea);
);
out geom;
