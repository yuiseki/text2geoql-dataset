[out:json][timeout:30];
area["name:en"="Dubai"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;