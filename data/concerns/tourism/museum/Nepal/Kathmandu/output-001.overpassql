[out:json][timeout:30];
area["name:en"="Kathmandu"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;