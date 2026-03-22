[out:json][timeout:30];
area["name:en"="Singapore"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;