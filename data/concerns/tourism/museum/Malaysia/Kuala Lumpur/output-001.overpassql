[out:json][timeout:30];
area["name:en"="Kuala Lumpur"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;