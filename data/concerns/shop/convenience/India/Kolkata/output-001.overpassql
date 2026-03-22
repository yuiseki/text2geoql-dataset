[out:json][timeout:30];
area["name:en"="Kolkata"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;