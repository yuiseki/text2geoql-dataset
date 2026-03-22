[out:json][timeout:30];
area["name:en"="Ulsan"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;