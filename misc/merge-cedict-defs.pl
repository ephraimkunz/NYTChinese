#!perl

#################
# In the original CC-CEDICT, some entries have an English definition consisting of only a reference; e.g., "See xxx" or "Variant of "xxx".
# These definitions aren't very useful when looking up a definition, so this program looks up the referring value and plugs it in where
# it is found in the reference
#

binmode STDOUT, ":utf8";


print <<EOF;
#################
# In the original CC-CEDICT, some entries have an English definition consisting of only a reference; e.g., "See xxx" or "Variant of "xxx".
# These definitions aren't very useful when looking up a definition, so this program looks up the referring value and plugs it in where
# it is found in the reference
#
EOF


my $DICTFILE = 'G:/Home/Chinese/Dictionaries/cedict_ts.u8';

my %dict;  # "trad:simp:pinyin" => "english"
my %partialdict;  # store trad and simp as headwords, to suggest correct targets for invalid references
my @wordorder;

open(DICT, "<:utf8", $DICTFILE) or die $!;

# Note: this is simplified-centric regarding merging same characters
while (<DICT>) {
    next unless /\w/;
    next if /^\s*#/;
    chomp;

    # U00b7 is a Middle Dot (for foreign names)
    unless (m|^(\S+)\s(\S+)\s\[([a-zA-Z0-9,\x{b7}: ]+)\]\s/(.*)/\s*$| ) {
        warn "Line $.: Invalid entry '$_'\n";
        next;
    }

    my ($trad, $simp, $pinyin, $english) = ($1, $2, $3, $4);

    if (defined $dict{"$trad:$simp:$pinyin"}) {
        print "# Error (merge-cedict-defs.pl): Repeat definition of '$trad:$simp:$pinyin' -- using the original and ignoring this one\n";
        next;
    }
    
    $dict{"$trad:$simp:$pinyin"} = [$trad, $simp, $pinyin, $english];
    $partialdict{$trad} = [$trad, $simp, $pinyin, $english];
    $partialdict{$simp} = [$trad, $simp, $pinyin, $english] if $trad ne $simp;
    push @wordorder, "$trad:$simp:$pinyin";
}


&CanonifyDictReferences();

print "#\n#\n";

foreach my $key ( @wordorder ) {
    if ($dict{$key}->[3] ne '') {
        print &cedictLine($dict{$key}->[0], $dict{$key}->[1], $dict{$key}->[2], $dict{$key}->[3]), "/\n";
    }
}

sub CanonifyDictReferences {

    foreach my $key (keys %dict) {
        my ($trad1, $simp1, $pinyin1, $english1) = @{$dict{$key}};
        
        my @replace_full = ();
        foreach my $english2 (split("/", $english1)) {         # $e2 is each subdefinition of every entry

            my ($trad2, $simp2, $pinyin2);
            # note: "abbr. for" isn't needed because they generally include the actual def'n. (%%TODO fill in the ones that are reference only)
            # note 2: "abbr. to", "related to", "see also", "also written", "also" are just notes
            # note 3: %%TODO "same as" is sometimes re-only, sometimes a note
            if ($english2 =~ /^(see|variant of|erhua variant of|archaic variant of|old variant of|ancient variant of|Japanese variant of|same as|abbr\. for) [a-zA-Z0-9\(\) ]*([^\[\|]+)\[([^\]]+)\]$/) {   # /see trad[pinyin]
                ($trad2, $simp2, $pinyin2) = ($2, $2, $3);
            } elsif ($english2 =~ /^(see|variant of|erhua variant of|archaic variant of|old variant of|ancient variant of|Japanese variant of|same as|abbr\. for) [a-zA-Z0-9\(\) ]*([^\|\[]+)\|([^\|\[]+)\[([^\]]+)\]$/) {   # /see trad|simp[pinyin]
                ($trad2, $simp2, $pinyin2) = ($2, $3, $4);
            }
            
            if (defined($trad2) and $trad2 !~ /^\s*also /) {  # 
                # If this is a "see xx[xx]" entry. The test doesn't need to be trad2, it's just detecting the regexp match
                #if ($"$BASECHAR"1) ARRGGGHHH
                if ($simp1 eq $simp2) {
                    #push @replace_full, '*DELETED-REDUNDANT*'; # don't add it to @replace_full, so it's effectively removed
                } else {
                    #look up the referral and append it
                    if (!exists $dict{"$trad2:$simp2:$pinyin2"}) {
                        print "# Error (merge-cedict-defs.pl): Invalid reference:\t",
                            "$trad1|$simp1\[$pinyin1\]\t",
                            "$english2\t",
                            "$trad2:$simp2:$pinyin2\t",
                            &cedictLine($trad1, $simp1, $pinyin1, $english1), "/\t",
                            &cedictLine(@{$partialdict{$trad2}}), "\t",
                            &cedictLine(@{$partialdict{$simp2}}),
                        "\n";
;
                        push @replace_full, $english2 . ', (*reference not found*)';
                    } else {
                        push @replace_full, $english2 . ', ' . $dict{"$trad2:$simp2:$pinyin2"}->[3];
                    }
                }
            } else {
                # a plain old entry
                push @replace_full, $english2;
            }
        }
          
        $dict{$key}->[3] = join('/', @replace_full);
    }
}


sub cedictLine {
    my ($trad, $simp, $pinyin, $english) = @_;
    return $trad, ' ', $simp, ' [', $pinyin, '] /', $english;
}
