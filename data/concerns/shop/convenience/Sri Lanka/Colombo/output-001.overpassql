[out:json][timeout:30];
area["name:en"="Colombo"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;