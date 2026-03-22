[out:json][timeout:30];
area["name:en"="Singapore"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;