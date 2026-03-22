[out:json][timeout:30];
area["name:en"="Casablanca"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;