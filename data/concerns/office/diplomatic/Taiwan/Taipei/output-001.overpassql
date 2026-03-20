[out:json][timeout:30];
area["name:en"="Taipei"]->.searchArea;
(
  nwr["office"="diplomatic"](area.searchArea);
);
out geom;
