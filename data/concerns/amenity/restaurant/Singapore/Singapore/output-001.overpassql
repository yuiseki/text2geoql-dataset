[out:json][timeout:30];
area["name:en"="Singapore"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;