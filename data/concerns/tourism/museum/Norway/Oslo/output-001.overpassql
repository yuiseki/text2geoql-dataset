[out:json][timeout:30];
area["name:en"="Oslo"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;