[out:json][timeout:30];
area["name:en"="Melbourne"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;