[out:json][timeout:30];
area["name:en"="Kuala Lumpur"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;