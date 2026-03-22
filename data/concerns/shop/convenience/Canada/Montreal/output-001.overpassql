[out:json][timeout:30];
area["name:en"="Montreal"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;