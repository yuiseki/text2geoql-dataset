[out:json][timeout:30];
area["name:en"="Dublin"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;