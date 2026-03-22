[out:json][timeout:30];
area["name:en"="Dublin"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;