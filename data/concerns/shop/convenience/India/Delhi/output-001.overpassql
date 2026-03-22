[out:json][timeout:30];
area["name:en"="Delhi"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;