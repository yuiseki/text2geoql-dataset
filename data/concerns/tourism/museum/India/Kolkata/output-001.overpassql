[out:json][timeout:30];
area["name:en"="Kolkata"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;