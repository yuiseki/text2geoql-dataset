[out:json][timeout:30];
area["name:en"="Lisbon"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;