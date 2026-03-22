[out:json][timeout:30];
area["name:en"="Dubai"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;