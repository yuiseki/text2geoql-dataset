[out:json][timeout:30];
area["name:en"="Auckland"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;