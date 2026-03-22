[out:json][timeout:30];
area["name:en"="Buenos Aires"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;