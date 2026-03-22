[out:json][timeout:30];
area["name:en"="Incheon"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;