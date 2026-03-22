[out:json][timeout:30];
area["name:en"="Prague"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;