[out:json][timeout:30];
area["name:en"="Kuala Lumpur"]->.searchArea;
(
  nwr["shop"="convenience"](area.searchArea);
);
out geom;