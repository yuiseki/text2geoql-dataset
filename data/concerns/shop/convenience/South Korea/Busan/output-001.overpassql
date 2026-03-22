[out:json][timeout:30];
area["name:en"="Busan"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;