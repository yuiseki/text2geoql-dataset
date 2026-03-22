[out:json][timeout:30];
area["name:en"="Montreal"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;