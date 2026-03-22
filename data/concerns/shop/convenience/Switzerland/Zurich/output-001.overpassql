[out:json][timeout:30];
area["name:en"="Zurich"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;