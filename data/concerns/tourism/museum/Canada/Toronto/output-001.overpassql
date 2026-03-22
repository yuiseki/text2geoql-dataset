[out:json][timeout:30];
area["name:en"="Toronto"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;