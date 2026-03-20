[out:json][timeout:30];
area["name:en"="Hong Kong"]->.searchArea;
(
  nwr["office"="diplomatic"](area.searchArea);
);
out geom;
