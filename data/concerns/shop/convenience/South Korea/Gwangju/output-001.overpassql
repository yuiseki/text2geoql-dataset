[out:json][timeout:30];
area["name:en"="Gwangju"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;