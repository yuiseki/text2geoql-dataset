[out:json][timeout:30];
area["name:en"="Tehran"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;