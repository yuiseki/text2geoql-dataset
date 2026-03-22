[out:json][timeout:30];
area["name:en"="Riyadh"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;